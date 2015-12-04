names={'oracle','random','sIL','sI','state','guess'};
N=length(names);
data=cell(N,1);
for j=1:N
    data{j}=dlmread(names{j},',');
    data{j}(data{j}>25)=25;
end
ave=[];
stds=[];
c=jet(N);
figure;subplot(1,2,2);
hold on
x=0:25;
for j=1:N
    counts=hist(data{j},x);
    plot(x,counts,'o-','color',c(j,:),'markerFaceColor',c(j,:));
    ave=[ave;mean(data{j})];
    stds=[stds;std(data{j})];
end
xlabel('score');
ylabel('frequency');
legend(names{:},'Location','NorthWest');
xlim([min(x) max(x)]);
box on;
grid on;
hold off
subplot(1,2,1);
errorbar(1:N,ave,stds,'ro');
grid on;
hold on
bar(1:N,ave);
set(gca,'xtick',1:N,'XTickLabel',names);
set(gcf,...
    'paperunit','inches',...
    'papersize',[3.3*2,2.8],...
    'paperposition',[0,0,3.3*2,2.8]);
print -dpdf data.pdf